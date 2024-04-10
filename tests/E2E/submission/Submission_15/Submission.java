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
        this.prices = prices;
        return dfs(0, 0);
    }

    int[] prices;

    private int dfs(int index, int state) {
        if (index == prices.length || state == 2)
            return 0;
        if (state == 0)
            // 不操作 买入
            return Math.max(dfs(index + 1, state), dfs(index + 1, state + 1) - prices[index]);
        // 不操作 卖出
        return Math.max(dfs(index + 1, state), dfs(index + 1, state + 1) + prices[index]);
    }
}
/*
tc01 [1] T
tc02 [7,6,4,3,1] T
tc03 [2,2,2,2,2,2] T
tc04 [1,10,1,10,1] T
tc05 [2,5] T
tc06 [5,2] T
tc07 [5,4,3,2,6] T
tc08 [6,4,3,2,5] T
tc09 [1,5,2,8,3] T
tc10 [0,0,1,0,0] T
*/

