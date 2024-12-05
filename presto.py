import re
import unicodedata
import regex
import regex


def tokenize_sentence(sentence):
    pattern = r'''
        [\p{L}\p{M}\p{Nd}]+       # Words: sequences of letters, combining marks, digits
        | '[^']*'                 # Text enclosed in single quotes, including quotes
        | [^\p{L}\p{M}\p{Nd}\s]+  # Punctuation and other symbols
    '''
    tokens = regex.findall(pattern, sentence, regex.VERBOSE)
    final_tokens = []
    for token in tokens:
        if token.startswith("'") and token.endswith("'") and len(token) > 2:
            # Split the content inside quotes
            final_tokens.append("'")
            content = token[1:-1]
            content_tokens = regex.findall(pattern, content, regex.VERBOSE)
            final_tokens.extend(content_tokens)
            final_tokens.append("'")
        else:
            final_tokens.append(token)
    return final_tokens

def tokenize_target(target_str):
    # (No changes needed here)
    tokens = []
    i = 0
    length = len(target_str)
    while i < length:
        c = target_str[i]
        if c == '(':
            tokens.append('(')
            i += 1
        elif c == ')':
            tokens.append(')')
            i += 1
        elif c == '«':
            i += 1
            start_i = i
            while i < length and target_str[i] != '»':
                i += 1
            value = target_str[start_i:i].strip()
            tokens.append(('QUOTED', value))
            i += 1  # Skip '»'
        elif c.isspace():
            i += 1
        else:
            # Collect word
            start_i = i
            while i < length and not target_str[i].isspace() and target_str[i] not in '()«»':
                i += 1
            word = target_str[start_i:i]
            tokens.append(('WORD', word))
    return tokens

def parse_tokens(tokens):
    # (No changes needed here)
    index = 0
    length = len(tokens)

    def parse_expression():
        nonlocal index
        if index >= length:
            return None
        token = tokens[index]
        if isinstance(token, tuple) and token[0] == 'WORD':
            name = token[1]
            index += 1
            if index < length and tokens[index] == '(':
                index += 1  # Skip '('
                args = parse_arguments()
                if index >= length or tokens[index] != ')':
                    raise ValueError("Expected ')'")
                index += 1  # Skip ')'
                return {'name': name, 'args': args}
            else:
                return name
        elif isinstance(token, tuple) and token[0] == 'QUOTED':
            index += 1
            return token[1]
        elif token == '(':
            index += 1
            expr = parse_expression()
            if index >= length or tokens[index] != ')':
                raise ValueError("Expected ')'")
            index +=1
            return expr
        else:
            raise ValueError(f"Unexpected token: {token}")

    def parse_arguments():
        nonlocal index
        args = {}
        while index < length and tokens[index] != ')':
            token = tokens[index]
            if isinstance(token, tuple) and token[0] == 'WORD':
                arg_name = token[1]
                index += 1
                if index < length and (tokens[index] == '(' or isinstance(tokens[index], tuple)):
                    arg_value = parse_expression()
                    args[arg_name] = arg_value
                else:
                    args[arg_name] = None
            else:
                index += 1  # Skip unexpected tokens
        return args

    result = parse_expression()
    return result

def extract_labels(parsed_structure, parent_label=''):
    # (No changes needed here)
    labels = []
    if isinstance(parsed_structure, dict):
        args = parsed_structure.get('args', {})
        for arg_name, arg_value in args.items():
            full_label = f"{parent_label}__{arg_name}" if parent_label else arg_name
            if isinstance(arg_value, dict):
                labels.extend(extract_labels(arg_value, full_label))
            else:
                labels.append((full_label, arg_value))
    return labels

def label_sentence(words, labels_values):
    labels = [0] * len(words)
    for label, value in labels_values:
        value_words = tokenize_sentence(value)
        n = len(words)
        m = len(value_words)
        for i in range(n - m + 1):
            if words[i:i + m] == value_words:
                for j in range(m):
                    labels[i + j] = label
                break  # Stop after first match
        else:
            # Case-insensitive matching
            words_lower = [w.lower() for w in words]
            value_words_lower = [w.lower() for w in value_words]
            for i in range(n - m + 1):
                if words_lower[i:i + m] == value_words_lower:
                    if all(labels[i + j] == 0 for j in range(m)):
                        for j in range(m):
                            labels[i + j] = label
                        break
    return labels
def parse_presto_labels(sentence, target):
    tokens = tokenize_target(target)
    print(f"Tokens: {tokens}")
    parsed_structure = parse_tokens(tokens)
    print(f"Parsed Structure: {parsed_structure}")
    task = parsed_structure.get('name', '')
    labels_values = extract_labels(parsed_structure)
    print(f"Labels Values: {labels_values}")
    words = tokenize_sentence(sentence)
    print(f"Words: {words}")
    labels = label_sentence(words, labels_values)
    print(f"Labels: {labels}")
    result = {
        'sentence': sentence,
        'words': words,
        'labels': labels,
        'task': task
    }
    return result
def parse_presto_labels(sentence, target):
    tokens = tokenize_target(target)
    print(f"Tokens: {tokens}")
    parsed_structure = parse_tokens(tokens)
    print(f"Parsed Structure: {parsed_structure}")
    task = parsed_structure.get('name', '')
    labels_values = extract_labels(parsed_structure)
    print(f"Labels Values: {labels_values}")
    words = tokenize_sentence(sentence)
    print(f"Words: {words}")
    labels = label_sentence(words, labels_values)
    print(f"Labels: {labels}")
    result = {
        'sentence': sentence,
        'words': words,
        'labels': labels,
        'task': task
    }
    return result
