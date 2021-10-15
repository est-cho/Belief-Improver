import argparse
import xml.etree.ElementTree as ET
import globals
import csv


DEFAULT_TIME_RANGE = 5
DEFAULT_VAR_RANGE = 5
DEFAULT_CONS_RANGE = 5

def convert_statement_to_string(prefix, s):
    out = prefix + str(s.index) + ': (' + s.p_left.v_left.type + '(i=' + str(s.p_left.v_left.index) + ', t=' + str(s.p_left.v_left.time) + ')' + s.p_left.op
    out = out + s.p_left.v_right.type + '(i=' + str(s.p_left.v_right.index) + ', t=' + str(s.p_left.v_right.time) + '),\t'
    out = out + s.p_right.v_left.type + '(i=' + str(s.p_right.v_left.index) + ', t=' + str(s.p_right.v_left.time) + ')' + s.p_right.op
    out = out + s.p_right.v_right.type + '(i=' + str(s.p_right.v_right.index) + ', t=' + str(s.p_right.v_right.time) + '))'
    return out

def calculate_score(name, statement, variable_data, const_values):
    if statement.p_left.v_left.type == globals.VAL_TYPE_VAR:
        lp_lv = variable_data[statement.p_left.v_left.index]
        lp_lv_t = statement.p_left.v_left.time
    else:
        lp_lv = [const_values[statement.p_left.v_left.index]]*len(variable_data[statement.p_left.v_left.index])
        lp_lv_t = 0
    
    if statement.p_left.v_right.type == globals.VAL_TYPE_VAR:
        lp_rv = variable_data[statement.p_left.v_right.index]
        lp_rv_t = statement.p_left.v_right.time
    else:
        lp_rv = [const_values[statement.p_left.v_right.index]]*len(variable_data[statement.p_left.v_right.index])
        lp_rv_t = 0

    if statement.p_right.v_left.type == globals.VAL_TYPE_VAR:
        rp_lv = variable_data[statement.p_right.v_left.index]
        rp_lv_t = statement.p_right.v_left.time
    else:
        rp_lv = [const_values[statement.p_right.v_left.index]]*len(variable_data[statement.p_right.v_left.index])
        rp_lv_t = 0
    
    if statement.p_right.v_right.type == globals.VAL_TYPE_VAR:
        rp_rv = variable_data[statement.p_right.v_right.index]
        rp_rv_t = statement.p_right.v_right.time
    else:
        rp_rv = [const_values[statement.p_right.v_right.index]]*len(variable_data[statement.p_right.v_right.index])
        rp_rv_t = 0

    data_len = [len(lp_lv), len(lp_rv), len(rp_lv), len(rp_rv)]
    time_len = [lp_lv_t, lp_rv_t, rp_lv_t, rp_rv_t]

    min_len = min(data_len) - max(time_len)

    tp = 0 # true positive
    tn = 0 # true negative
    fp = 0 # false positive
    fn = 0 # false negative
    for i in range(min_len):
        first_left  = lp_lv[i + lp_lv_t]
        first_right = lp_rv[i + lp_rv_t]
        first = globals.OPERATOR_DICT[statement.p_left.op](first_left, first_right)
        second_left = rp_lv[i + rp_lv_t]
        second_right = rp_rv[i + rp_rv_t]
        second = globals.OPERATOR_DICT[statement.p_right.op](second_left, second_right)
        if first and second:
            tp += 1
        elif first and not second:
            tn += 1
        elif not first and second:
            fp += 1
        elif not first and not second:
            fn += 1
        
    if (tp + tn) == 0:
        score = 0
    else: 
        score = float(tp) / float(tp + tn) * 100.0
    
    statement_string = convert_statement_to_string(name, statement)
    return (statement_string, tp, tn, fp, fn, score)


def parse_input_xml(original):
    og_root = ET.parse(original).getroot()
    for p in og_root.findall('parameter'):
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
    for s in og_root.findall(globals.TAG_STATEMENT): # Find all statements
        s_idx = int(s.attrib[globals.ATTRIB_NAME].split('_')[1])
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
        
        statement = globals.Statement(s_idx, lp, rp)
        s_list.append(statement)
    return (param, s_list)

def parse_mutated_xml(mutated):
    m_root = ET.parse(mutated).getroot()
    pair_list = []
    for input_s in m_root.findall(globals.TAG_INPUT): # Find input statement
        input_index = int(input_s.attrib[globals.ATTRIB_NAME].split('_')[1])

        m_list = []
        for m in input_s.findall(globals.TAG_STATEMENT): # Find mutated statement
            s_idx = int(m.attrib[globals.ATTRIB_NAME].split('_')[1])
            lp = globals.Prop()
            rp = globals.Prop()
            for p in m.findall(globals.TAG_PROP): # Find all propositions
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
            
            statement = globals.Statement(s_idx, lp, rp)
            m_list.append(statement)
        pair_list.append((input_index, m_list))
    return pair_list

def evaluate(param, s_list, pair_list, data_file, output_prefix):
    file = open(data_file,'r',encoding = 'utf-8-sig')
    data = csv.reader(file)
    const_header = next(data)
    const_values_raw = next(data)
    const_values = []
    for x in range(param.constant_range):
        const_values.append(float(const_values_raw[x]))
    var_header = next(data)
    variable_data = [[] for i in range(param.variable_range)]
    for (j, line) in enumerate(data):
        for i in range(param.variable_range):
            variable_data[i].append(float(line[i]))
    
    new_pair_list = []
    for pair in pair_list:
        for original_s in s_list:
            if original_s.index == pair[0]:
                new_pair_list.append((original_s, pair[1]))
                break
    
    for new_pair in new_pair_list:
        file_prefix = output_prefix + 'o_' + str(new_pair[0].index) + '_'
        og_eval = calculate_score('o_', new_pair[0], variable_data, const_values)

        mutated_statements = []
        m_eval_list = []
        for m in new_pair[1]:
            m_eval = calculate_score('m_', m, variable_data, const_values)
            m_eval_list.append(m_eval)
        
        improved = []
        for m in sorted(m_eval_list, key=lambda x: (x[5]), reverse=True):
            if m[5] >= og_eval[5]:
                improved.append(m)
            else:
                break

        with open(file_prefix + 'evaluation.csv', 'w', newline='') as csvfile: 
            csv_writer = csv.writer(csvfile) 
            csv_writer.writerow(['Original Statement', 'tp', 'tn', 'fp', 'fn', 'score'])
            csv_writer.writerow(og_eval)
            csv_writer.writerow(['Alternative Statements', 'tp', 'tn', 'fp', 'fn', 'Score'])
            for m in sorted(m_eval_list, key=lambda x: (x[5]), reverse=True):
                csv_writer.writerow(m)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluator')
    parser.add_argument('-i', '--initial', required=True)
    parser.add_argument('-m', '--mutated', required=True)
    parser.add_argument('-d', '--data', required=True)
    parser.add_argument('-o', '--output-prefix', required=False)
    
    args = parser.parse_args()

    output_prefix = ''
    if args.output_prefix:
        output_prefix = args.output_prefix + '_'
    
    (param, s_list) = parse_input_xml(args.initial)
    pair_list = parse_mutated_xml(args.mutated)
    evaluate(param, s_list, pair_list, args.data, output_prefix)
    
