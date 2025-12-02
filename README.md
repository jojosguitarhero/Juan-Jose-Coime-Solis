import java.util.Scanner;

public class Series_Fibonacci {
    public static void main(String[] args) {
        Scanner sc = new Scanner (System.in);
            int n;

            System.out.print("Ingrese n: ");
            n = sc.nextInt();

            double suma = 0;
            
            int f1 = 0, f2 = 1, fn = 0;

            for (int i = 1; i <= n; i++) {
            
                if (i == 1) fn = 0;
                else if (i == 2) fn = 1;
                else {
                    fn = f1 + f2;
                    f1 = f2;
                    f2 = fn;
                }

                double termino = 0;

                boolean conRaiz = (i == 2 || i == 3 || (i >= 7 && i <= 10));

                if (conRaiz) {
                    termino = Math.sqrt((double) fn / i);
                } else {
                
                    int exp = 2;
                    if (i == 4) exp = 7;
                    if (i == 5) exp = 11;
                    if (i == 6) exp = 13;
                    if (i == 11) exp = 31;

                    termino = Math.pow(fn, exp) / i;
                }

                if (i % 2 == 0) suma -= termino;
                else suma += termino;

                System.out.println("Termino " + i + " = " + termino);
            }

            System.out.println("\nSuma total S = " + suma);
        }
    }
