"""
@file doxyfilter-cache.py

Doxygen Filter for Cache ObjectScript

This Python script serves as a Doxygen filter for parsing and converting Cache ObjectScript code into quasi-C++ code with Doxygen comments.
The filtered code can then be used for generating documentation using Doxygen.

Usage:
  python doxyfilter-cache.py <input-file> [--debug]

Arguments:
  - <input-file>: The path to the input Cache ObjectScript file to be filtered.
  - [--debug]: Optional flag to enable debugging mode. If specified, the filtered code will be saved to an output file.

Filtering Process:
- The script parses Cache ObjectScript code and identifies classes, methods, properties, parameters, indexes, and XData blocks.
- It generates C++-like code with Doxygen comments to provide documentation for each code element.
- The generated code can be used with Doxygen to generate documentation.

Global Flags and Variables:
- Global flags are used to track the context while parsing the code.
- Global variables store the content for different code elements.

Regular Expressions:
- The script uses regular expressions to match and extract comments and comment characters from the code.

Functions:
- append_line(target, line, indent=True): Appends a line to the target string with optional indentation.
- convert_type(type): Converts Cache ObjectScript data types to C++ data types.
- extract_additional_data(line): Extracts additional data (metadata) from a line of code.
- check_keyword(line, keyword): Checks if a keyword is present in a line of code.
- format_method_signature(line): Formats the signature of a method.
- format_xdata_signature(line): Formats the signature of an XData block.
- handle_xdata_mimetype(line): Handles the MIME type of an XData block.
- handle_class(line): Handles the definition of a class.
- handle_param_type(line): Determines the C++ data type for a parameter.
- handle_param_or_property(line): Handles parameters and properties.
- handle_index(line): Handles index definitions.
- handle_method(line): Handles method definitions.
- handle_xdata(line): Handles XData blocks.
- handle_storage(line): Handles Storage blocks.
- parse(input_file): Main function to parse the input Cache ObjectScript file.

Command-Line Usage:
- The script can be run from the command line with the following parameters:
  - <input-file>: The path to the Cache ObjectScript input file to be filtered.
  - [--debug]: Optional flag to enable debugging mode. If specified, the filtered code is saved to an output file.

Output:
- The filtered and formatted code is generated and can be saved to an output file or displayed on the console.
- When used with Doxygen, this code generates documentation for Cache ObjectScript code.

Note:
- This script is intended to be used as a preprocessor with Doxygen for documenting Cache ObjectScript code.
"""

import re
import sys

# Global flags
inside_class_block = False
inside_classmethod_block = False
inside_method_block = False
inside_xdata_block = False
inside_storage_block = False
inside_comment_block = False
inside_xdata_block = False
inside_xdata_content = False
inside_xdata_css_content = False
private_method = False
abstract_method = False

# Global variables for storing content
file_content = ""
class_content = ""
method_content = ""
method_signature = ""
xdata_signature = ""
parameter_content = ""
property_content = ""
xdata_content = ""
index_content = ""
comments = ""
xdata_mimetype = ""
public_content = "public:\n\n"
private_content = "private:\n\n"

intendation = 4

# Regular expressions
# Match lines containing comments
comment_pattern = re.compile(r'((?://[^\n]*)|(/\*.*?\*/))', re.DOTALL)
# Match only the comment characters // /* /// //// etc
comment_chars_pattern = re.compile(r'((?://+))', re.DOTALL)

def append_line(target, line, indent=True):
    """
    Appends a line of text to the target string, with optional indentation.

    Args:
        target (str): The target string to which the line will be appended.
        line (str): The line of text to be appended to the target.
        indent (bool, optional): Whether to apply indentation before appending the line. Defaults to True.

    Returns:
        str: The updated target string with the appended line.
    """
    global intendation

    if indent:
        target += (" " * intendation) + line
    else:
        target += line

    return target


def convert_type(type):
    """
    Converts a basic type string to its corresponding format.

    Args:
        type (str): The input type string to be converted.

    Returns:
        str: The converted type string.
    """
    # Convert basic types
    if type in "STRING":
        type = "%String"
    elif type in "INTEGER":
        type = "%Integer"
    elif type in "BOOLEAN":
        type = "%Boolean"
    return type

def extract_additional_data(line):
    """
    Extracts additional data and keyword data from a line of code.

    Args:
        line (str): The input line of code to extract data from.

    Returns:
        str: A formatted string containing extracted data.

    Raises:
        Exception: If an unknown type is encountered in the input line.
    """    
    result = ""
    member_keyword_data = ""
    member_additional_data = ""
    data = line.strip().split()
    type = data.pop(0)
    
    if type in ["Property", "Parameter"]:
        name = data.pop(0).strip(";")
        if data:
            part = data.pop(0)
            if "As" in part:
                type = data.pop(0).strip().strip(";")
                if "(" in type:
                    member_additional_data = (type + " " + (" ".join(data))).split("(")[1].split(")")[0].strip().split(", ")
                    result += "/// Member Additional Data:<br>\n"
                    result += "".join([f"/// > {d.strip()}<br>\n" for d in member_additional_data])
                    data = " ".join(data).split(")")
                    data.pop(0)
                    if data: # if we still have data left to process
                        part = data.pop(0).strip()
                        if "[" in part:
                            member_keyword_data = (part + " " + (" ".join(data))).split("[")[1].split("]")[0].strip().split(", ")
                            result += "/// Member Keyword Data:<br>\n"
                            result += "".join([f"/// > {d.strip()}<br>\n" for d in member_keyword_data])
            elif "[" in part:
                member_keyword_data = (part + " " + (" ".join(data))).split("[")[1].split("]")[0].strip().split(", ")
                result += "/// Member Keyword Data:\n"
                result += "".join([f"/// > {d.strip()}\n" for d in member_keyword_data])
    elif "Method" in type:
        name = data.pop(0)
        if "(" in name:
            data = " ".join(data).split(")")
            data.pop(0)
            if data: # if we still have data left to process
                part = data.pop(0).strip()
                if "[" in part:
                    member_keyword_data = (part + " " + (" ".join(data))).split("[")[1].split("]")[0].strip().split(", ")
                    result += "/// Member Keyword Data:<br>\n"
                    result += "".join([f"/// > {d.strip()}<br>\n" for d in member_keyword_data])
    elif "Index" in type:
        name = data.pop(0)
        data = " ".join(data).strip()
        member_additional_data = data.split("[")[0].strip()
        member_keyword_data = data.split("[")
        if len(member_keyword_data) > 1:
            member_keyword_data = member_keyword_data[1].split("]")[0].strip().split(", ")
        else:
            member_keyword_data = None
        if member_additional_data:
            result += f"/// Member additional data:<br>\n"
            result += f"/// > {member_additional_data}<br>\n"
        if member_keyword_data:
            result += f"/// Member keyword data:<br>\n"
            result += "".join([f"/// > {d.strip()}<br>\n" for d in member_keyword_data])
    elif "XData" in type:
        data = " ".join(data).strip()
        if "[" in data:
            member_keyword_data = data.split("[")[1].split("]")[0].split(", ")
            result += f"/// Member keyword data:<br>\n"
            result += "".join([f"/// > {d.strip()}<br>\n" for d in member_keyword_data])
    else:
        raise Exception(f"Unknown type: {type}")
    return result

def check_keyword(line, keyword):
    """
    Checks if a given keyword is present in a line of code.

    Args:
        line (str): The input line of code to check for the keyword.
        keyword (str): The keyword to check for.

    Returns:
        bool: True if the keyword is found, False otherwise.

    Raises:
        Exception: If an unknown type is encountered in the input line.
    """
    #print (f"Checking for keyword: {keyword} from line {line}")
    keywords = ""
    data = line.replace(" as ", " As ").strip().split()
    type = data.pop(0)
    if type in ["Property", "Parameter"]:
        name = data.pop(0).strip(";")
        if data:
            part = data.pop(0)
            if "As" in part:
                type = data.pop(0).strip().strip(";")
                if "(" in type:
                    data = " ".join(data).split(")")
                    data.pop(0)
                    if data: # if we still have data left to process
                        part = data.pop(0).strip()
                        if "[" in part:
                            keywords = " ".join(data).split("]")[0].strip().split(", ")
            elif "[" in part:
                keywords = " ".join(data).split("]")[0].split(", ")
    elif "Method" in type:
        data = " ".join(data).split(")")
        data.pop(0)
        if data: # if we still have data left to process
            part = data.pop(0).strip()
            if "[" in part:
                keywords = part.strip().split("[")[1].split("]")[0].split(", ")
    elif type in "Class":
        if "[" in data:
            keywords = " ".join(data).split("[")[1].split("]")[0].strip().split(", ")
    else:
        raise Exception(f"Trying to parse keywords from an unknown type: {type}")

    if keywords:
        keywords = [k.strip() for k in keywords]
        if keyword in keywords:
            return True
    else:
        return False

def format_method_signature(line):
    """
    Formats a method signature line into a standard format.

    Args:
        line (str): The input line containing a method signature.

    Returns:
        str: The formatted method signature.

    Raises:
        Exception: If an invalid method signature is encountered.
    """
    signature = ""
    line = line.strip().replace(" as ", " As ")
    #print(f"Parsing method signature: {line}")
    if line.startswith("ClassMethod"):
        type = line.split(")")
        if len(type) > 1:
            type = type[1].lstrip().split("As")
            if len(type) > 1:
                type = type[1].lstrip().split(" ")[0].strip(";")
            else:
                type = "void"
        name = line.split(")")[0].split("ClassMethod")[1].strip() + ")"
        signature = f"static {type} {name}"
        #print(f"Signature: {signature}")

    elif line.startswith("Method"):
        type = line.split(")")
        if len(type) > 1:
            type = type[1].lstrip().split("As")
            if len(type) > 1:
                type = type[1].lstrip().split(" ")[0].strip(";")
            else:
                type = "void"
        name = line.split(")")[0].split("Method")[1].strip() + ")"
        signature = f"{type} {name}"
        #print(f"Signature: {signature}")
        if check_keyword(line, "Abstract"):
            signature = f"virtual {signature}"
    elif line.startswith("ClientMethod"):
        type = line.split(")")
        if len(type) > 1:
            type = type[1].lstrip().split("As")
            if len(type) > 1:
                type = type[1].lstrip().split(" ")[0].strip(";")
            else:
                type = "void"
        name = line.split(")")[0].split("ClientMethod")[1].strip() + ")"
        signature = f"{type} {name}"
        #print(f"Signature: {signature}")
    else:
        raise Exception("Invalid method signature")
    return signature

def format_xdata_signature(line):
    """
    Formats an XData signature line into a standard format.

    Args:
        line (str): The input line containing an XData signature.

    Returns:
        str: The formatted XData signature.

    Raises:
        Exception: If an invalid XData signature is encountered.
    """    
    signature = ""
    type = "XData"
    name = ""
    #print(f"Parsing xdata signature: {line}")
    if line.startswith("XData "):
        name = line.split("XData ")[1].split(" ")[0].strip()
        signature = f"{type} {name};"
        #print(f"Signature: {signature}")
    else:
        raise Exception("Invalid xdata signature")
    #print(f"XData signature: {signature}") 
    return signature

def handle_xdata_mimetype(line):
    """
    Extracts the Mimetype value from an XData line.

    Args:
        line (str): The input line containing XData information.

    Returns:
        str: The extracted Mimetype value.

    Note:
        If no Mimetype is found, it defaults to "application/xml".
    """
    #print(f"Looking for XData Mimetype in line: {line.strip()}")
    mimetype = line.split("[")
    if len(mimetype) > 1:
        if "MimeType" in mimetype[1]:
            mimetype = mimetype[1].split("MimeType = ")[1].split("]")[0].strip()
            #print(f"XData Mimetype resolved: {mimetype}")
        else:
            mimetype = "application/xml"
    else:
        mimetype = "application/xml" # Default mimetype if no mimetype is found
        #print(f"Using default mimetype: {mimetype}")

    return mimetype

def handle_class(line):
    """
    Handles the parsing of a 'Class' line.

    Args:
        line (str): The input line containing 'Class' information.

    """
    global public_content
    global class_content
    class_full_name = line.split(" ")[1]
    class_name = class_full_name.split(".")[-1]
    class_definition = f"class {class_full_name}".strip()

    # Check for directives
    if check_keyword(line, "Abstract"):
        public_content = append_line(public_content, "virtual ~" + class_name + "() = 0;\n\n")

    extends = line.split("Extends")
    if len(extends) > 1:
        extends = extends[1].split("[")[0].strip().strip("()").split(",")
        extends = [e.strip() for e in extends]
        class_definition = append_line(class_definition, " :", False)
        for e in extends:
            class_definition = append_line(class_definition, f" public {e},", False)
        class_definition = class_definition.strip(",")
    class_content = class_definition + "\n"

def handle_param_type(line):
    """
    Handles the parsing of a parameter type from a line.

    Args:
        line (str): The input line containing parameter information.

    Returns:
        str: The parsed parameter type.
    """
    type = "%String" # Default value
    try:
        if line in ["0", "1"]:
            type = "%Boolean"
        else:
            line = int(line)
            type = "%Integer"
    except ValueError:
        type = "%String"
    return type

def handle_param_or_property(line):
    """
    Handles the parsing of parameter or property lines.

    Args:
        line (str): The input line containing parameter or property information.
    """
    global parameter_content
    global property_content
    global public_content
    global private_content

    result = ""

    data = line.strip().replace(" as ", " As ").split()

    # Sanity checks
    if not data:
        raise Exception("Trying to parse an empty line")
    if data[0] not in ["Parameter", "Property"]:
        raise Exception(f"Trying to parse a line which is not either Parameter or Property, or line is empty. Data: {data}")

    line_type = data.pop(0) # Remove first index containing the keyword
    name = data.pop(0).strip(";")
    type = "%String" # Default value
    value = "\"\"" # Default value

    if data:
        part = data.pop(0)
        if "=" in part:
            value = " ".join(data).strip().strip(";")
            type = handle_param_type(value)
        elif "As" in part:
            type = data.pop(0).strip().strip(";")
            if "(" in type:
                type = type.split("(")[0]
                data = " ".join(data).split(")")
                data.pop(0)
            if data: # if we still have data left to process
                part = data.pop(0).strip()
                if "[" in part:
                    data = " ".join(data).split("]")
                    data.pop(0)
                    if data: # if we still have data left to process
                        part = data.pop(0).strip()
                        if "=" in part:
                            value = " ".join(data).strip().strip(";")
                elif "=" in part:
                    value = " ".join(data).strip().strip(";")
        elif "[" in part:
            data = " ".join(data).split("]")
            data.pop(0)
            if data: # if we still have data left to process
                part = data.pop(0).strip()
                if "=" in part:
                    value = " ".join(data).strip().strip(";")

    if line_type in "Parameter":
        result = f"const {type} {name} = {value};"
    else:
        result = f"{type} {name};"

    # Check if theres a comment after the semicolon
    comment = ""
    match = comment_pattern.search(line)
    if match:
        comment = match.group(0)

    additional_data = extract_additional_data(line)
    
    if line_type in "Parameter":
        result = f"const {type} {name} = {value}; {comment}\n"
        parameter_content = append_line(parameter_content, additional_data, False)
        parameter_content = append_line(parameter_content, result, False)
        parameter_content = "\n".join([(" ") * intendation + l for l in parameter_content.strip().split('\n')]) # Indent content
        public_content = append_line(public_content, parameter_content + "\n\n", False)
        parameter_content = ""
    else:
        result = f"{type} {name}; {comment}\n"
        property_content = append_line(property_content, additional_data, False)
        property_content = append_line(property_content, result, False)
        property_content = "\n".join([(" ") * intendation + l for l in property_content.strip().split('\n')]) # Indent content
        if check_keyword(line, "Private"):
            private_content = append_line(private_content, property_content + "\n\n", False)
        else:
            public_content = append_line(public_content, property_content + "\n\n", False)
        property_content = ""

def handle_index(line):
    """
    Handles the parsing of an 'Index' line.

    Args:
        line (str): The input line containing 'Index' information.
    """
    global index_content
    global public_content

    result = ""
    data = line.strip().split()
    
    # Sanity check
    if data[0] not in ["Index"]:
        raise Exception(f"Trying to parse an index line which is not Index. Data: {data}")
    
    data.pop(0) # Remove first index containing the keyword
    name = data.pop(0).strip().strip(";")
    additional_data = extract_additional_data(line)
    result = f"Index {name};" 

    index_content = append_line(index_content, additional_data, False)
    index_content = append_line(index_content, result, False)
    index_content = "\n".join([(" ") * intendation + l for l in index_content.strip().split('\n')]) # Indent content
    public_content = append_line(public_content, index_content + "\n\n", False)
    index_content = ""

def handle_method(line):
    """
    Handles the parsing of method lines.

    Args:
        line (str): The input line containing method information.
    """
    global inside_method_block
    global inside_classmethod_block
    global method_content
    global method_signature
    global abstract_method
    global private_method
    global private_content
    global public_content
    if line.startswith("{"):
        method_content = append_line(method_content, line, False)
    elif line.startswith("}"):
        method_content = append_line(method_content, line, False)
        method_content = "\n".join([(" ") * intendation + m for m in method_content.strip().split('\n')]) # Indent method content
        #print(f"Method signature: {method_signature}")
        #print(f"Method Content:\n{method_content}")
        #print(f"Abstract: {abstract_method}")
        #print(f"Private: {private_method}")
        if private_method:
            if abstract_method:
                private_content = append_line(private_content, "/// Note: this is an Abstract method\n", True)
            private_content = append_line(private_content, method_content + "\n" + "\n", False)
        else:
            if abstract_method:
                public_content = append_line(public_content, "/// Note: this is an Abstract method\n", True)
            public_content = append_line(public_content, method_content + "\n" + "\n", False)
        abstract_method = False
        private_method = False
        if "static" in method_signature:
            inside_classmethod_block = False
        else:
            inside_method_block = False
        method_signature = ""
        method_content = ""
    else:
        comment = ""
        match = comment_pattern.search(line)
        if match:
            comment = match.group(0)
            comment.strip("\n")
            match = comment_chars_pattern.search(comment)
            if match:
                comment_chars = match.group(0)
                comment = "/// " + comment.split(comment_chars)[1].strip()
            method_content = append_line(method_content, comment + "\n", True)

def handle_xdata(line):
    """
    Handles the parsing of XData lines.

    Args:
        line (str): The input line containing XData information.
    """
    global inside_xdata_block
    global inside_xdata_content
    global inside_xdata_css_content
    global xdata_content
    global public_content
    global xdata_mimetype
    if line.startswith("{"):
        if not inside_xdata_content:
            inside_xdata_content = True
            xdata_content += f"/// XData content:\n"
            xdata_content += f"/// ```\n"  
        elif xdata_mimetype in "application/json":
            line = line.strip("\n") # Remove possible newline at the end of the line
            xdata_content += f"/// {line}\n"
    elif line.startswith("<style"):
        inside_xdata_css_content = True
        line = line.strip("\n") # Remove possible newline at the end of the line
        xdata_content += f"/// {line}\n"
    elif line.startswith("</style>"):
        inside_xdata_css_content = False
        line = line.strip("\n")
        xdata_content += f"/// {line}\n"
    elif line.startswith("}"):
        if inside_xdata_css_content:
            line = line.strip("\n")
            xdata_content += f"/// {line}\n"
        elif inside_xdata_content and xdata_mimetype in "application/json":
            line = line.strip("\n") # Remove possible newline at the end of the line
            xdata_content += f"/// {line}\n"
            inside_xdata_content = False
        else:
            inside_xdata_content = False
            inside_xdata_block = False
            xdata_content += f"/// ```\n"
            xdata_content += f"{xdata_signature}"
            xdata_content = "\n".join([(" ") * intendation + l for l in xdata_content.strip().split('\n')]) # Indent content
            public_content = append_line(public_content, xdata_content + "\n\n", False)
    else:
        line = line.strip("\n") # Remove possible newline at the end of the line
        xdata_content += f"/// {line}\n"
        return

def handle_storage(line):
    """
    Handles the parsing of 'Storage' lines.

    Args:
        line (str): The input line containing 'Storage' information.
    """
    global inside_storage_block
    if line.startswith("{"):
        return
    if line.startswith("}"):
        inside_storage_block = False
        return
    else:
        return

def parse(input_file):
    """
    Parses the input file and generates a quasi-C++ content.

    Args:
        input_file (str): The path to the input file to be parsed.
    """
    global inside_xdata_block
    global inside_class_block
    global inside_storage_block
    global inside_classmethod_block
    global inside_method_block
    global inside_comment_block
    global method_content
    global method_signature
    global xdata_content
    global xdata_signature
    global parameter_content
    global property_content
    global class_content
    global file_content
    global public_content
    global private_content
    global comments
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.replace("\t", " " * intendation).replace(" ; ", "/// ").replace("#; ", "/// ")
            if line.startswith("Class "):
                inside_class_block = True
                handle_class(line)
                continue
            elif line.startswith("Include "):
                line = "/// " + line.strip() + "\n"
                file_content = append_line(file_content, line, False)
                continue
            elif inside_xdata_block:
                handle_xdata(line)
                continue
            elif inside_storage_block:
                handle_storage(line)
                continue
            elif inside_classmethod_block:
                handle_method(line)
                continue
            elif inside_method_block:
                handle_method(line)
                continue
            elif inside_class_block:
                if line.startswith("Property "):
                    if comments.strip() != "":
                        property_content = append_line(property_content, comments, False)
                        comments = ""
                    handle_param_or_property(line)
                    continue
                elif line.startswith("Parameter "):
                    if comments.strip() != "":
                        parameter_content = append_line(parameter_content, comments, False)
                        comments = ""
                    handle_param_or_property(line)
                    continue
                elif line.startswith("Index "):
                    if comments.strip() != "":
                        method_content = append_line(method_content, comments, False)
                        comments = ""
                    handle_index(line)
                    continue
                elif line.startswith("ClassMethod "):
                    inside_classmethod_block = True
                    private_method = check_keyword(line, "Private")

                    if comments.strip() != "":
                        method_content = append_line(method_content, comments, False)
                        comments = ""
                    
                    additional_data = extract_additional_data(line)
                    if additional_data.strip() != "":
                        method_content = append_line(method_content, additional_data, False)

                    method_signature = format_method_signature(line)
                    method_content = append_line(method_content, method_signature + "\n", False)
                    continue
                elif line.startswith("Method ") or line.startswith("ClientMethod "):
                    inside_method_block = True
                    abstract_method = check_keyword(line, "Abstract")
                    private_method = check_keyword(line, "Private")
                    
                    if comments.strip() != "":
                        method_content = append_line(method_content, comments, False)
                        comments = ""
                    
                    if line.startswith("ClientMethod "):
                        remark = "///This method is a ClientMethod. Any instance method defined with the keyword ClientMethod\n" \
                                    "///becomes a client-side instance method of the client page object.\n" \
                                    "///When called, it executes within the browser.\n"
                        method_content = append_line(method_content, remark, False)
                    
                    additional_data = extract_additional_data(line)
                    if additional_data.strip() != "":
                        method_content = append_line(method_content, additional_data, False)
                    
                    method_signature = format_method_signature(line)                    
                    method_content = append_line(method_content, method_signature + "\n", False)
                    continue
                elif line.startswith("XData "):
                    inside_xdata_block = True
                    xdata_mimetype = handle_xdata_mimetype(line)
                    xdata_signature = format_xdata_signature(line)
                    if comments.strip() != "":
                        xdata_content = append_line(xdata_content, comments, False)
                    comments = ""

                    additional_data = extract_additional_data(line)
                    if additional_data.strip() != "":
                        xdata_content = append_line(xdata_content, additional_data, False)
                    continue
                elif line.startswith("Storage "):
                    inside_storage_block = True
                    continue
                elif line.startswith("}"):
                    inside_class_block = False
                    if public_content.strip() != "public:":
                        class_content = append_line(class_content, public_content + "\n", False)
                    if private_content.strip() != "private:":
                        class_content = append_line(class_content, private_content + "\n", False)
                    if comments.strip() != "":
                        file_content = append_line(file_content, comments + "\n", False)
                    #print(f"Class Content: {class_content}")
                    #print(f"Public Content: {public_content}")
                    #print(f"Private Content: {private_content}")
                    class_content = append_line(class_content, line, False)
                    file_content = append_line(file_content, class_content, False)
                    break
                else:
                    comment  = ""
                    match = comment_pattern.search(line)
                    if match:
                        comment = match.group(0)
                        comments = append_line(comments, comment + "\n", False)
                        #print (f"Comment: {comment}")
                    elif line.startswith("/*"):
                        comment = line.strip().replace("/*", "///")
                        inside_comment_block = True
                        comments = append_line(comments, comment + "\n", False)
                        #print (f"Comment: {comment}")
                    elif inside_comment_block:
                        comment = line.strip().strip("\n")
                        if comment:
                            if "*/" in comment:
                                comment = comment.replace("*/", "///")
                                inside_comment_block = False
                                comments = append_line(comments, comment, False)
                                #print (f"Comment: {comment}")
                            elif comment.startswith("*"):
                                comment = comment.replace("*", "///")
                                comments = append_line(comments, comment + "\n", False)
                                #print (f"Comment: {comment}")
                            else:
                                comments = append_line(comments, "/// " + comment + "\n", False)
                                #print (f"Comment: {comment}")
                    else:
                        line = line.strip()
                        if line:
                            class_content += line + "\n"
                        else:
                            if comments.strip() != "":
                                file_content = append_line(file_content, comments, False)
                                comments = ""
                continue
            else:
                file_content += line

if __name__ == "__main__":
    # Ensure proper command-line usage
    if len(sys.argv) < 2:
        print("Usage: python cachefilter.py <input-file> [--debug]")
        sys.exit(1)

    input_file = sys.argv[1]
    debug_flag = sys.argv[2] if len(sys.argv) > 2 else None
    output_file = test = "./output/" + input_file.split("/")[-1].split(".")[0] + ".cpp"

    if debug_flag is not None and debug_flag in "--debug":
        debug = True
    else:
        debug = False

    parse(input_file)

    if debug:
        with open(output_file, "w", encoding="utf-8") as file:
            print(f"Writing filtered ObjectScript to file: {output_file}")
            file.write(file_content)
    else:
        sys.stdout.buffer.write(file_content.encode('utf-8'))
        sys.stdout.flush()
