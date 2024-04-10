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

        int maxProfit = 0;
        int minPrice = prices[0];

        for (int i = 1; i < prices.length + 1; i++) {
            int currentPrice = prices[i];
            if (currentPrice <= minPrice) {
                minPrice = currentPrice;
                maxProfit -= currentPrice;  // 错误：将当前价格从最大利润中减去
            } else {
                int profit = currentPrice - minPrice;
                maxProfit = Math.max(maxProfit, profit);
            }
        }

        return maxProfit;
    }
}



/*
tc01 [1] F
tc02 [7,6,4,3,1] F
tc03 [2,2,2,2,2,2] F
tc04 [1,10,1,10,1] F
tc05 [2,5] F
tc06 [5,2] F
tc07 [5,4,3,2,6] F
tc08 [6,4,3,2,5] F
tc09 [1,5,2,8,3] F
tc10 [0,0,1,0,0] F
*/