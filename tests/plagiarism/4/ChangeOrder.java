import java.io.*;
import java.util.*;

public class ChageOrder {

    public ArrayList<String> inputExpressions;
    public ArrayList<String> calculationResults;
     public ChangeOrder() {
        calculationResults = new ArrayList<>();
        inputExpressions = new ArrayList<>();
    }
    private void performOperation(Deque<Integer> numberStack, Deque<Character> operatorStack) {
        while (!operatorStack.isEmpty() && (operatorStack.peek() == '*' || operatorStack.peek() == '/')) {
            int operand2 = numberStack.pop();
            int operand1 = numberStack.pop();
            char op = operatorStack.pop();
            int result = op == '*' ? operand1 * operand2 : operand1 / operand2;
            numberStack.push(result);
        }
    }

    public void calculate(String path) {
        read_file(path);
        for (String expression : inputExpressions) {
            cal(expression);
        }
        write_file("Out.txt");
    }
  public void write_file(String path) {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(path));
            for (String line : calculationResults) {
                writer.write(line);
                writer.newLine();
            }
            writer.close();
        } catch (IOException e) {
            System.out.println("An error occurred while writing to file.");
            e.printStackTrace();
        }
    }

    public void read_file(String path) {
        try {
            File file = new File(path);
            FileInputStream fis = new FileInputStream(file);
            StringBuilder builder = new StringBuilder();
            int content;
            while ((content = fis.read()) != -1) {
                char charContent = (char) content;
                if (charContent == '\n') {
                    inputExpressions.add(builder.toString());
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
  
     public void cal(String expression) {
        if (!Character.isDigit(expression.charAt(0)) || !Character.isDigit(expression.charAt(expression.length() - 1))) {
            calculationResults.add("Error");
            return;
        }
        Deque<Character> operatorStack = new ArrayDeque<>();
        Deque<Integer> numberStack = new ArrayDeque<>();
        int currentNumber = 0;

        for (char c : expression.toCharArray()) {
            if (Character.isDigit(c)) {
                currentNumber = currentNumber * 10 + c - '0';
            } else {
                numberStack.push(currentNumber);
                currentNumber = 0;
                if (c == '+' || c == '-' || c == '*' || c == '/') {
                    performOperation(numberStack, operatorStack);
                    operatorStack.push(c);
                } else {
                    System.out.println("Wrong input");
                    return;
                }
            }
        }
        numberStack.push(currentNumber);
        performOperation(numberStack, operatorStack);

        int result = 0;
        while (!operatorStack.isEmpty()) {
            result += operatorStack.pop() == '+' ? numberStack.pop() : -numberStack.pop();
        }
        result += numberStack.pop();
        calculationResults.add(Integer.toString(result));
    }
}
