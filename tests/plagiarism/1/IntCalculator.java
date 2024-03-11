import java.io.*;
import java.util.*;

public class IntCalculator {

    public ArrayList<String> input;
    public ArrayList<String> output;

    public IntCalculator() {
        input = new ArrayList<>();
        output = new ArrayList<>();
    }

    public void calculate(String path) {
        read_file(path);
        for (String expression : input) {
            cal(expression);
        }
        write_file("Out.txt");//write the output into out.txt
    }

    public void cal(String expression) {
        StringBuilder add_sub_exp = new StringBuilder();// create a new array
        if (!Character.isDigit(expression.charAt(0))) {
            output.add("Error");
            return;
        }
        if (!Character.isDigit(expression.charAt(expression.length() - 1))) {
            output.add("Error");
            return;
        }
        for (int i = 0; i < expression.length(); i++) {
            char c = expression.charAt(i);
            if (!Character.isDigit(c)) {
                if (c != '*' && c != '-' && c != '+' && c != '/') {
                    output.add("Error");
                    return;
                } else if (!Character.isDigit(expression.charAt(i + 1))) {
                    output.add("Error");
                    return;
                }
            }
        }
        Deque<Integer> nums = new ArrayDeque<>();
        Deque<Character> operators = new ArrayDeque<>();
        int num = 0;
        for (char c : expression.toCharArray()) {
            if (c >= '0' && c <= '9') {//read the number
                num = num * 10 + c - '0';//Constructed new number
            } else {
                nums.push(num);
                if (!operators.isEmpty()) {//first do the multiply and divide
                    switch (operators.peek()) {
                        case '*':
                            operators.pop();
                            int b = nums.pop();
                            int a = nums.pop();
                            nums.push(a * b);
                            break;
                        case '/':
                            operators.pop();
                            int y = nums.pop();
                            int x = nums.pop();
                            nums.push(x / y);
                    }
                }
                if (c == '+' || c == '-' || c == '*' || c == '/')
                    operators.push(c);
                else//Invalid input, return int minimum value
                    System.out.println("Wrong");
                num = 0;
            }
        }
        //Add the last constructed number and monitor multiplication and division
        nums.push(num);
        if (!operators.isEmpty()) {
            switch (operators.peek()) {
                case '*':
                    operators.pop();
                    int b = nums.pop();
                    int a = nums.pop();
                    nums.push(a * b);
                    break;
                case '/':
                    operators.pop();
                    int y = nums.pop();
                    int x = nums.pop();
                    if (y == 0) {//zero cannot be dividend
                        output.add("Error");
                        return;
                    }
                    nums.push(x / y);
            }
        }
        int result = 0;
        //addition and subtraction
        while (!operators.isEmpty()) {
            char op = operators.pop();
            if (op == '+') {
                result += nums.pop();
            } else
                result -= nums.pop();
        }
        result += nums.pop();
        output.add(Integer.toString(result));
        return;
    }

    public void read_file(String path) {
        try {
            File file = new File(path);
            FileInputStream fis = new FileInputStream(file);
            int content;
            int count = 0;
            StringBuilder builder = new StringBuilder();
            while ((content = fis.read()) != -1) {
                if ((char) content == ' ') {
                    continue;
                }
                if ((char) content == '\n') {
                    input.add(builder.toString());
                    builder = new StringBuilder();
                    count++;
                    continue;
                }
                builder.append((char) content);
            }
            fis.close();
        } catch (IOException e) {
            System.out.println("An IOException happens while reading from a file: " + path);
        }
    }//cannot find the file

    public void write_file(String path) {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(path));
            for (String line : output) {
                writer.write(line);
                writer.newLine(); // change a new line
            }
            writer.close();
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }
}