 import java.util.*;

public class Submission {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String string = sc.nextLine();
        String[] array  = string.split(" ");

        int prices[] = new int[array.length];
        for (int i = 0; i < prices.length; i++) {
            prices[i] = Integer.valueOf(array[i]);
        }

        System.out.println(maxProfit(prices)); 
    }




    public static int maxProfit(int[] prices) {
        if (prices.length <= 2) {
            return prices[0];
        }
        int maxProfit = 0;
        int minPrice = prices[0];
        for (int i = 1; i < prices.length; i++) {
            if (prices[i] < minPrice) {
                minPrice = prices[i];
            } else {
                maxProfit += prices[i] - minPrice;
            }
        }
        return maxProfit;
    }
}
/*
tc01 [1] F
tc02 [7,6,4,3,1] T
tc03 [2,2,2,2,2,2] T
tc04 [1,10,1,10,1] F
tc05 [2,5] F
tc06 [5,2] F
tc07 [5,4,3,2,6] T
tc08 [6,4,3,2,5] T
tc09 [1,5,2,8,3] F
tc10 [0,0,1,0,0] T
*/