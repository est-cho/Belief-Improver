import argparse
import xml.etree.ElementTree as ET
import globals


DEFAULT_TIME_RANGE = 5
DEFAULT_VAR_RANGE = 5
DEFAULT_CONS_RANGE = 5

def parse_xml(file_name):
    root = ET.parse(file_name).getroot()

    for p in root.findall('parameter'):
        time_range = 0
        if p.find('timeRange') is None:
            time_range = DEFAULT_TIME_RANGE
        else:
            time_range = int(p.find('timeRange').text)
        
        variable_range = 0
        if p.find('variableRange') is None:
            variable_range = DEFAULT_VAR_RANGE
        else:
            variable_range = int(p.find('variableRange').text)
        
        constant_range = 0
        if p.find('constantRange') is None:
            constant_range = DEFAULT_CONS_RANGE
        else:
            constant_range = int(p.find('constantRange').text)

    param = globals.Parameter(time_range, variable_range, constant_range)
    
    s_list = []
    for s in root.findall('statement'): # Find all statements
        index = int(s.attrib[globals.ATTRIB_NAME].split('_')[1])
        lp = globals.Prop()
        rp = globals.Prop()
        for p in s.findall(globals.TAG_PROP): # Find all propositions
            lv = globals.Value()
            rv = globals.Value()
            for pf in p.findall(globals.TAG_VALUE): # Find left and right values in the proposition
                if pf.attrib[globals.ATTRIB_NAME] == globals.ATTRIB_LEFT:
                    if pf.find(globals.TAG_TIME) is None:
                        lv = globals.Value(pf.find(globals.TAG_TYPE).text, int(pf.find(globals.TAG_INDEX).text))
                    else:
                        lv = globals.Value(pf.find(globals.TAG_TYPE).text, int(pf.find(globals.TAG_INDEX).text), int(pf.find(globals.TAG_TIME).text))
                else:
                    if pf.find(globals.TAG_TIME) is None:
                        rv = globals.Value(pf.find(globals.TAG_TYPE).text, int(pf.find(globals.TAG_INDEX).text))
                    else:
                        rv = globals.Value(pf.find(globals.TAG_TYPE).text, int(pf.find(globals.TAG_INDEX).text), int(pf.find(globals.TAG_TIME).text))
            op = p.find(globals.TAG_OP).text
        
            if p.attrib[globals.ATTRIB_NAME] == globals.ATTRIB_LEFT:
                lp = globals.Prop(lv, op, rv)
            else:
                rp = globals.Prop(lv, op, rv)
        
        statement = globals.Statement(index, lp, rp)
        s_list.append(statement)

    return (param, s_list)

def mutate(param, s_list):
    pair_list = []
    for s in s_list:
        mut_s = []
        # Mutate operators
        # Operator Mutation on Left Proposition
        lp_op = s.p_left.op
        i = globals.OPERATORS.index(lp_op)
        
        for j in [x for x in range(len(globals.OPERATORS)) if x != i]:
            copy_s = s.copy()
            copy_s.p_left.op = globals.OPERATORS[j]
            mut_s.append(copy_s)

        # Operator Mutation on Right Proposition
        rp_op = s.p_right.op
        i = globals.OPERATORS.index(rp_op)

        for j in [x for x in range(len(globals.OPERATORS)) if x != i]:
            copy_s = s.copy()
            copy_s.p_right.op = globals.OPERATORS[j]
            mut_s.append(copy_s)
        
        v_list = [s.p_left.v_left, s.p_left.v_right, s.p_right.v_left, s.p_right.v_right]

        for (i, v) in enumerate(v_list):
            mut_v = []
            if v.type == globals.VAL_TYPE_VAR:
                for j in [x for x in range(param.variable_range) if x != v.index]:
                    copy_v = v.copy()
                    copy_v.index = j
                    mut_v.append(copy_v)
                for j in [x for x in range(param.time_range) if x != v.time]:
                    copy_v = v.copy()
                    copy_v.time = j
                    mut_v.append(copy_v)
            else:
                for j in [x for x in range(param.constant_range) if x != v.index]:
                    copy_v = v.copy()
                    copy_v.index = j
                    mut_v.append(copy_v)
            
            for mv in mut_v:
                copy_s = s.copy()
                if i == 0:
                    copy_s.p_left.v_left = mv
                    mut_s.append(copy_s)
                elif i == 1:
                    copy_s.p_left.v_right = mv
                    mut_s.append(copy_s)
                elif i == 2:
                    copy_s.p_right.v_left = mv
                    mut_s.append(copy_s)
                else:
                    copy_s.p_right.v_right = mv
                    mut_s.append(copy_s)
        pair_list.append((s, mut_s))    
    return pair_list

def convert_to_xml(outfile_name, pair_list):
    body = ET.Element(globals.TAG_BODY)

    for (s, mut_s) in pair_list:
        original_s = ET.SubElement(body, globals.TAG_INPUT, name= 'o_' + str(s.index))
        for (i, m) in enumerate(mut_s):
            t_state = ET.SubElement(original_s, globals.TAG_STATEMENT, name='m_' + str(i))
            p_left = ET.SubElement(t_state, 'prop', name='left')
            p_l_v_left = ET.SubElement(p_left, 'value', name='left')
            ET.SubElement(p_l_v_left, 'type').text = m.p_left.v_left.type
            ET.SubElement(p_l_v_left, 'index').text = str(m.p_left.v_left.index)
            if m.p_left.v_left.time is not None:
                ET.SubElement(p_l_v_left, 'time').text =  str(m.p_left.v_left.time)

            ET.SubElement(p_left, 'op').text = str(m.p_left.op)

            p_l_v_right = ET.SubElement(p_left, 'value', name='right')
            ET.SubElement(p_l_v_right, 'type').text = m.p_left.v_right.type
            ET.SubElement(p_l_v_right, 'index').text = str(m.p_left.v_right.index)
            if m.p_left.v_right.time is not None:
                ET.SubElement(p_l_v_right, 'time').text =  str(m.p_left.v_right.time)

            p_right = ET.SubElement(t_state, 'prop', name='right')
            p_r_v_left = ET.SubElement(p_right, 'value', name='left')
            ET.SubElement(p_r_v_left, 'type').text = m.p_right.v_left.type
            ET.SubElement(p_r_v_left, 'index').text = str(m.p_right.v_left.index)
            if m.p_right.v_left.time is not None:
                ET.SubElement(p_r_v_left, 'time').text =  str(m.p_right.v_left.time)

            ET.SubElement(p_right, 'op').text = str(m.p_right.op)

            p_r_v_right = ET.SubElement(p_right, 'value', name='right')
            ET.SubElement(p_r_v_right, 'type').text = m.p_right.v_right.type
            ET.SubElement(p_r_v_right, 'index').text = str(m.p_right.v_right.index)
            if m.p_right.v_right.time is not None:
                ET.SubElement(p_r_v_right, 'time').text =  str(m.p_right.v_right.time)


    tree = ET.ElementTree(body)
    ET.indent(tree, space='    ')
    tree.write(outfile_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mutator')
    parser.add_argument('-i', '--initial', required=True)
    parser.add_argument('-o', '--output-name', required=False)
    
    args = parser.parse_args()

    name = args.output_name 
    if name is None:
        name = "out_mutated.xml"
    elif 'xml' not in name:
        name += '.xml'

    (param, s_list) = parse_xml(args.initial)
    pair_list = mutate(param, s_list)
    convert_to_xml(name, pair_list)
