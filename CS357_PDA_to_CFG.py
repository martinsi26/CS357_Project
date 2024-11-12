import csv
import json

def create_pda_json(states, input_alphabet, stack_alphabet, transitions, start_state, final_states):
    pda = {
        "states": states,
        "input_symbols": input_alphabet,
        "stack_symbols": stack_alphabet,
        "transitions": transitions,
        "initial_state": start_state,
        "final_states": final_states
    }
    return pda

def read_pda_from_csv(filename):
    states = []
    input_alphabet = []
    stack_alphabet = []
    transitions = {}
    start_state = None
    final_states = []

    with open(filename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header row

        for row in csv_reader:
            component, *values = row

            if component == "states":
                states.extend(values)
            elif component == "input_alphabet":
                input_alphabet.extend(values)
            elif component == "stack_alphabet":
                stack_alphabet.extend(values)
            elif component == "transitions":
                current_state, input_symbol, stack_symbol, next_state, stack_operation = values
                # Organize transitions as a nested dictionary
                if current_state not in transitions:
                    transitions[current_state] = {}
                if input_symbol not in transitions[current_state]:
                    transitions[current_state][input_symbol] = {}
                transitions[current_state][input_symbol][stack_symbol] = (next_state, stack_operation)
            elif component == "initial_state":
                start_state = values[0]
            elif component == "final_states":
                final_states.extend(values)

    # Return the dictionary directly from create_pda_json
    return create_pda_json(states, input_alphabet, stack_alphabet, transitions, start_state, final_states)

def check_pda(pda_json):
    """
    Checks the validity of the PDA JSON.
    This function will validate the following:
    - All required components are present (non-empty).
    - Transitions use valid states, symbols from the input alphabet, and symbols from the stack alphabet.
    - Each transition is in the correct format (state, input symbol, stack symbol, state, stack operation).
    - The initial state exists in the states list.
    - All final states exist in the states list.
    - "epsilon" cannot be used as a state, input symbol, stack symbol, initial state, or final state.
    """
    
    states = set(pda_json["states"])
    input_symbols = set(pda_json["input_symbols"])
    stack_symbols = set(pda_json["stack_symbols"])
    
    # Check that no component is empty
    if not pda_json["states"]:
        raise ValueError("States cannot be empty.")
    if not pda_json["input_symbols"]:
        raise ValueError("Input alphabet cannot be empty.")
    if not pda_json["stack_symbols"]:
        raise ValueError("Stack alphabet cannot be empty.")
    if not pda_json["transitions"]:
        raise ValueError("Transitions cannot be empty.")
    if pda_json["initial_state"] is None:
        raise ValueError("Initial state cannot be None.")
    if not pda_json["final_states"]:
        raise ValueError("Final states cannot be empty.")
    
    # Check that "epsilon" is not used in invalid locations
    if "epsilon" in states:
        raise ValueError("The empty string 'epsilon' cannot be used as a state.")
    if "epsilon" in input_symbols:
        raise ValueError("The empty string 'epsilon' cannot be used as an input symbol.")
    if "epsilon" in stack_symbols:
        raise ValueError("The empty string 'epsilon' cannot be used as a stack symbol.")
    if pda_json["initial_state"] == "epsilon":
        raise ValueError("The empty string 'epsilon' cannot be used as the initial state.")
    if "epsilon" in pda_json["final_states"]:
        raise ValueError("The empty string 'epsilon' cannot be used as a final state.")
    
    # Ensure states do not overlap with input symbols or stack symbols
    overlapping = states & (input_symbols | stack_symbols)
    if overlapping:
        raise ValueError(f"States cannot overlap with input symbols or stack symbols: {', '.join(overlapping)}")
    
    # Ensure input symbols and stack symbols do not overlap
    overlapping_symbols = input_symbols & stack_symbols
    if overlapping_symbols:
        raise ValueError(f"Input symbols and stack symbols cannot overlap: {', '.join(overlapping_symbols)}")
    
    # Ensure initial state is a valid state
    if pda_json["initial_state"] not in states:
        raise ValueError(f"Initial state '{pda_json['initial_state']}' is not a valid state.")
    
    # Validate final states
    for state in pda_json["final_states"]:
        if state not in states:
            raise ValueError(f"Final state '{state}' is not a valid state.")
    
    # Validate transitions
    for current_state, input_symbol_dict in pda_json["transitions"].items():
        if current_state not in states:
            raise ValueError(f"Transition state '{current_state}' is not a valid state.")
        
        for input_symbol, stack_symbol_dict in input_symbol_dict.items():
            if input_symbol != "epsilon" and input_symbol not in input_symbols:
                raise ValueError(f"Transition input symbol '{input_symbol}' is not a valid input symbol.")
            
            for popped_symbol, (next_state, pushed_symbol) in stack_symbol_dict.items():
                if popped_symbol != "epsilon" and popped_symbol not in stack_symbols:
                    raise ValueError(f"Transition popped symbol '{popped_symbol}' is not a valid stack symbol.")
                if next_state not in states:
                    raise ValueError(f"Transition next state '{next_state}' is not a valid state.")
                if pushed_symbol != "epsilon" and pushed_symbol not in stack_symbols:
                    raise ValueError(f"Transition pushed symbol '{pushed_symbol}' is not a valid stack symbol.")
    
    # Additional check for initial state not being in input_symbols or stack_symbols
    if pda_json["initial_state"] in input_symbols or pda_json["initial_state"] in stack_symbols:
        raise ValueError(f"Initial state '{pda_json['initial_state']}' cannot be in input symbols or stack symbols.")
    
    # Ensure no final state is used as an input symbol or stack symbol
    for final_state in pda_json["final_states"]:
        if final_state in input_symbols or final_state in stack_symbols:
            raise ValueError(f"Final state '{final_state}' cannot be in input symbols or stack symbols.")
    
    # Ensure input symbols do not contain states
    for input_symbol in input_symbols:
        if input_symbol in states:
            raise ValueError(f"Input symbol '{input_symbol}' cannot be a state.")
    
    # Ensure stack symbols do not contain states
    for stack_symbol in stack_symbols:
        if stack_symbol in states:
            raise ValueError(f"Stack symbol '{stack_symbol}' cannot be a state.")

    print("PDA is valid.")
    
    return pda_json

def create_cfg_json(variables, alphabet, rules, start_variable):
    cfg = {
        "variables": variables,
        "alphabet": alphabet,
        "rules": rules,
        "start_variable": start_variable
    }
    return cfg

def write_cfg_to_csv(cfg, filename='output.csv'):
    with open(filename, mode='w') as file:
        # Write the header with the space after the comma
        file.write("Component, Values\n")
        
        # Variables
        file.write(f"Variables: {{{' '.join(cfg['variables'])}}}\n")
        
        # Alphabet
        file.write(f"Alphabet: {{{' '.join(cfg['alphabet'])}}}\n")
        
        # Rules
        for lhs, rhs_list in cfg["rules"].items():
            for rhs in rhs_list:
                file.write(f"Rule: {lhs} -> {' '.join(rhs)}\n")
        
        # Start Variable
        file.write(f"Start Variable: {cfg['start_variable']}\n")
        
def update_pda(pda_json):
    # Step 1: Check if there is only one final state
    if len(pda_json["final_states"]) == 1:
        print("Only one final state, proceeding with updates.")
    else:
        print("There are multiple final states. Updates will be made later.")

    # Step 2: Check if the final transition empties the stack
    stack_operations = {}
    
    # Track all stack operations (pushes and pops)
    for current_state, input_symbol_dict in pda_json["transitions"].items():
        for input_symbol, popped_symbol_dict in input_symbol_dict.items():
            for popped_symbol, (next_state, pushed_symbol) in popped_symbol_dict.items():
                # Track push operations
                if pushed_symbol != 'ϵ':  # If it's not epsilon, it's a push
                    if pushed_symbol not in stack_operations:
                        stack_operations[pushed_symbol] = {'pushed': 0, 'popped': 0}
                    stack_operations[pushed_symbol]['pushed'] += 1
                
                # Track pop operations
                if popped_symbol != 'ϵ':  # If it's not epsilon, it's a pop
                    if popped_symbol not in stack_operations:
                        stack_operations[popped_symbol] = {'pushed': 0, 'popped': 0}
                    stack_operations[popped_symbol]['popped'] += 1

    # Check if any pushed symbol was not popped
    for stack_symbol, operations in stack_operations.items():
        if operations['pushed'] > operations['popped']:
            print(f"Stack symbol '{stack_symbol}' was pushed but never fully popped. The stack needs to be emptied.")
    
    # Step 3: Check for transitions where the stack stays the same
    for current_state, input_symbol_dict in pda_json["transitions"].items():
        for input_symbol, popped_symbol_dict in input_symbol_dict.items():
            for popped_symbol, (next_state, pushed_symbol) in popped_symbol_dict.items():
                # Check if both the push and pop operations are the same
                if popped_symbol == pushed_symbol:
                    print(f"There is a problem with the transition at {current_state} with input symbol '{input_symbol}'. "
                          f"The stack symbol '{popped_symbol}' is both pushed and popped, so the stack stays the same.")
    
    return pda_json

def convert_pda_to_cfg(pda_json):
    variables = []
    alphabet = []
    rules = []
    start_variable = None

    pda_json = update_pda(pda_json)
    
    return create_cfg_json(variables, alphabet, rules, start_variable)

# Convert CSV to JSON and print the result
pda_json = read_pda_from_csv('input.csv')
pda_json = check_pda(pda_json)
print(pda_json)
pda_json = update_pda(pda_json)
#cfg_json = convert_pda_to_cfg(pda_json)

# Write CFG JSON to CSV
#write_cfg_to_csv(cfg_json)