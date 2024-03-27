import java.io.*;
import java.util.*;

public class ChangeALot {

    // Lists to store expressions and results
    public ArrayList<String> aaaaa;
    public ArrayList<String> bbbbb;

    // Constructor to initialize the lists
    public ChangeALot() {
        aaaaa = new ArrayList<>();
        bbbbb = new ArrayList<>();
    }

    // Evaluates the given arithmetic expression
    public void b(String expression) {
        // Checks if the expression starts and ends with a digit
        if (!Character.isDigit(expression.charAt(0)) || !Character.isDigit(expression.charAt(expression.length() - 1))) {
            bbbbb.add("Error");
            return;
        }

        // Stack for numbers and operators
        Deque<Integer> ccccc = new ArrayDeque<>();
        Deque<Character> operatorStack = new ArrayDeque<>();

        // Variable to store the current number being processed
        int ooooooo = 0;
        for (char c : expression.toCharArray()) {
            // Accumulate digit to form a number
            if (Character.isDigit(c)) {
                ooooooo = ooooooo * 10 + c - '0';
            } else {
                // Push the number onto the stack and evaluate if possible
                ccccc.push(ooooooo);
                if (!operatorStack.isEmpty()) {
                    ppppp(ccccc, operatorStack);
                }

                // Push the operator onto the stack
                if (c == '+' || c == '-' || c == '*' || c == '/') {
                    operatorStack.push(c);
                } else {
                    // Invalid input
                    System.out.println("Wrong input");
                    return;
                }
                ooooooo = 0;
            }
        }
        // Push the last number to the stack and evaluate the remaining operations
        ccccc.push(ooooooo);
        if (!operatorStack.isEmpty()) {
            ppppp(ccccc, operatorStack);
        }

        // Compute the final result
        int rrrrr = 0;
        while (!operatorStack.isEmpty()) {
            char op = operatorStack.pop();
            if (op == '+') {
                rrrrr += ccccc.pop();
            } else {
                rrrrr -= ccccc.pop();
            }
        }
        rrrrr += ccccc.pop();
        bbbbb.add(Integer.toString(rrrrr));
    }

    // Reads expressions from a file
    public void a(String path) {
        rrrrr(path);
        for (String expression : aaaaa) {
            b(expression);
        }
        wwwwwwwwwww("Out.txt"); // write the output into out.txt
    }

    // Helper method to read from a file
    public void rrrrr(String path) {
        try {
            File file = new File(path);
            StringBuilder builder = new StringBuilder();
            FileInputStream fis = new FileInputStream(file);
            int content;
            while ((content = fis.read()) != -1) {
                char charContent = (char) content;
                // Add expression to list when a newline is encountered
                if (charContent == '\n') {
                    aaaaa.add(builder.toString());
                    builder = new StringBuilder();
                } else if (charContent != ' ') {
                    builder.append(charContent);
                }
            }
            fis.close();
        } catch (IOException e) {
            System.out.println("An IOException occurred while reading from file: " + path);
        }
    }

    // Helper method to perform an operation
    private void ppppp(Deque<Integer> ccccc, Deque<Character> operatorStack) {
        char op = operatorStack.pop();
        int operand2 = ccccc.pop();
        int operand1 = ccccc.pop();
        // Perform the operation based on the operator
        switch (op) {
            case '*':
                ccccc.push(operand1 * operand2);
                break;
            case '/':
                if (operand2 == 0) {
                    bbbbb.add("Error");
                    return;
                }
                ccccc.push(operand1 / operand2);
                break;
        }
    }

    // Writes results to a file
    public void wwwwwwwwwww(String path) {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(path));
            for (String line : bbbbb) {
                writer.write(line);
                writer.newLine();
            }
            writer.close();
        } catch (IOException e) {
            System.out.println("An error occurred while writing to file.");
            e.printStackTrace();
        }
    }
}
