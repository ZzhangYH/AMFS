import java.io.*;
import java.util.*;

public class ChangeVarName {

    public ArrayList<String> aaaaa;
    public ArrayList<String> bbbbb;

    public ChangeVarName() {
        aaaaa = new ArrayList<>();
        bbbbb = new ArrayList<>();
    }

    public void a(String path) {
        rrrrr(path);
        for (String expression : aaaaa) {
            b(expression);
        }
        wwwwwwwwwww("Out.txt"); // write the output into out.txt
    }

    public void b(String expression) {
        if (!Character.isDigit(expression.charAt(0)) || !Character.isDigit(expression.charAt(expression.length() - 1))) {
            bbbbb.add("Error");
            return;
        }

        Deque<Integer> ccccc = new ArrayDeque<>();
        Deque<Character> operatorStack = new ArrayDeque<>();
        int ooooooo = 0;
        for (char c : expression.toCharArray()) {
            if (Character.isDigit(c)) {
                ooooooo = ooooooo * 10 + c - '0';
            } else {
                ccccc.push(ooooooo);
                if (!operatorStack.isEmpty()) {
                    ppppp(ccccc, operatorStack);
                }
                if (c == '+' || c == '-' || c == '*' || c == '/') {
                    operatorStack.push(c);
                } else {
                    System.out.println("Wrong input");
                    return;
                }
                ooooooo = 0;
            }
        }
        ccccc.push(ooooooo);
        if (!operatorStack.isEmpty()) {
            ppppp(ccccc, operatorStack);
        }

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

    private void ppppp(Deque<Integer> ccccc, Deque<Character> operatorStack) {
        char op = operatorStack.pop();
        int operand2 = ccccc.pop();
        int operand1 = ccccc.pop();
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

    public void rrrrr(String path) {
        try {
            File file = new File(path);
            FileInputStream fis = new FileInputStream(file);
            StringBuilder builder = new StringBuilder();
            int content;
            while ((content = fis.read()) != -1) {
                char charContent = (char) content;
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
