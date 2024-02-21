import java.util.ArrayList;
import java.util.Scanner;

public class IdSum {

    private static ArrayList<Integer> STUDENTS;

    private static void performOp(int opCode, int src, int dest) {
        if (opCode == 1) {
            move(src, dest, 0);
        } else if (opCode == 2) {
            move(src, dest, 1);
        } else if (opCode == 3) {
            swap(src, dest);
        }
    }

    private static void move(int x, int y, int offset) {
        int xIndex = STUDENTS.indexOf(x);
        STUDENTS.remove(xIndex);
        int yIndex = STUDENTS.indexOf(y);
        STUDENTS.add(yIndex + offset, x); // offset: 0 on the left, 1 on the right
    }

    private static void swap(int x, int y) {
        int xIndex = STUDENTS.indexOf(x);
        int yIndex = STUDENTS.indexOf(y);
        STUDENTS.set(xIndex, y);
        STUDENTS.set(yIndex, x);
    }

    private static int sumEven() {
        int sum = 0;
        for (int i = 1; i < STUDENTS.size(); i += 2) {
            sum += STUDENTS.get(i);
        }
        return sum;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int numOfStudents = scanner.nextInt();
        STUDENTS = new ArrayList<>(numOfStudents);
        for (int i = 1; i <= numOfStudents; i++) {
            STUDENTS.add(i);
        }

        int numOfOp = scanner.nextInt();
        for (int i = 0; i < numOfOp; i++) {
            int code = scanner.nextInt();
            int x = scanner.nextInt();
            int y = scanner.nextInt();
            performOp(code, x, y);
        }
        scanner.close();

        System.out.println(sumEven());
    }

}
