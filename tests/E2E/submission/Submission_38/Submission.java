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

    public static int maxProfit(int prices[]) {
        int n = prices.length;
        int dp[] = new int[n];
        dp[0] = 0;

        for (int i = 1; i < n; i++) {
            dp[i] = Math.max(dp[i-1], dp[i-1] + prices[i] - prices[i-1]);
        }

        return dp[n-1];
    }
}

/*
tc01 [1] T
tc02 [7,6,4,3,1] T
tc03 [2,2,2,2,2,2] T
tc04 [1,10,1,10,1] F
tc05 [2,5] T
tc06 [5,2] T
tc07 [5,4,3,2,6] T
tc08 [6,4,3,2,5] T
tc09 [1,5,2,8,3] F
tc10 [0,0,1,0,0] T
*/