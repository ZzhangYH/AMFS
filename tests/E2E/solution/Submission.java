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
        int minprice = Integer.MAX_VALUE;
        int maxprofit = 0;
        for (int i = 0; i < prices.length; i++) {
            if (prices[i] < minprice) {
                minprice = prices[i];
            } else if (prices[i] - minprice > maxprofit) {
                maxprofit = prices[i] - minprice;
            }
        }
        return maxprofit;
    }
}

/*
tc01 [1] output 0
tc02 [7,6,4,3,1] output 0
tc03 [2,2,2,2,2,2] output 0
tc04 [1,10,1,10,1] output 9
tc05 [2,5] output 3
tc06 [5,2] output 0
tc07 [5,4,3,2,6] output 4
tc08 [6,4,3,2,5] output 3
tc09 [1,5,2,8,3] output 7
tc10 [0,0,1,0,0] output 1
*/