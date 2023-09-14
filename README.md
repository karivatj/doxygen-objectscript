# Doxygen Filter for ObjectScript

This Doxygen filter allows you to generate documentation from ObjectScript code by converting it into quasi-C++ syntax and then providing it to Doxygen for further processing. The filter is written in Python.

## Usage and Test

1. Clone or download this repository to your local machine.

2. Make sure you have Python 3 installed on your system.

3. Run the filter script by executing the following command: 

```
python cachefilter.py <input-file> [--debug]
```

Replace `<input-file>` with the path to your ObjectScript code file. Optionally, you can use the `--debug` flag to generate a separate output file for debugging purposes. Omitting --debug will output the transformed class to stdout. This is the mode that is used when using the filter together with Doxygen.

4. The filter will process the ObjectScript code and convert it into C++-like code. If you used the `--debug` flag, you'll find the output in the `./output/` folder with the same name as your input file but with a `.cpp` extension.

# Generating documentation with Doxygen

1. Make sure you have Doxygen installed on your system. If not, you can download and install it from [Doxygen's official website](https://www.doxygen.nl/download.html).

2. Run Doxygen in the root of the project to generate the documentation. You can use the following command:

```
doxygen Doxyfile
```

3. The generated documentation will be placed in the `docs/html/` folder.

## Sample Code

The `src/` folder contains some example code you can use to test the implementation. The code has been fetched from [InterSystems Samples-ObjectScript repository](https://github.com/intersystems/Samples-ObjectScript). 

# Summary

The filter introduced here will provide the means to use Doxygen to generate documentation from ObjectScript classes.

Please note that this filter provides basic functionality for ObjectScript to C++ conversion for Doxygen. You may need to modify or extend it to meet your specific project's needs.

# Documentation

Documentation created from this repository can be found on this project's [GitHub Pages](https://karivatj.github.io/doxygen-objectscript). Please explore to see an example of the documentation that can be created from your ObjectScript classes with Doxygen.

If you have any questions or need assistance, please don't hesitate to reach out!
