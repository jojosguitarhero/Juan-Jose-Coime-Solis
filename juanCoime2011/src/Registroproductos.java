import java.util.Scanner;

public class Registroproductos {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int limiteProductos;
        int totalProductos = 0;
        double totalIVA = 0;
        double totalIMC = 0;
        double totalVentas = 0;

        // 1. Pedir límite máximo de productos
        System.out.print("Ingrese el límite máximo de productos para hoy: ");
        limiteProductos = sc.nextInt();

        // Validar límite (debe ser positivo)
        while (limiteProductos <= 0) {
            System.out.println("El límite debe ser un número positivo.");
            System.out.print("Ingrese nuevamente el límite máximo de productos: ");
            limiteProductos = sc.nextInt();
        }

        // Consumir el salto de línea pendiente
        sc.nextLine();

        // 5. Bucle para ingresar productos hasta llegar al límite
        for (int i = 1; i <= limiteProductos; i++) {
            System.out.println("\n--- Producto " + i + " ---");

            // 3. Leer nombre del producto
            System.out.print("Nombre del producto: ");
            String nombre = sc.nextLine();  // Aunque no se use en cálculos, se registra

            // 3. Leer precio base con validación (no negativo ni cero)
            double precioBase;
            System.out.print("Precio base: ");
            precioBase = sc.nextDouble();

            while (precioBase <= 0) {
                System.out.println("Error: el precio base debe ser un número positivo.");
                System.out.print("Ingrese nuevamente el precio base: ");
                precioBase = sc.nextDouble();
            }

            // 3. Leer si tiene IVA (0 o 1) con validación
            int tieneIVA;
            System.out.print("¿El producto tiene IVA? (1 = sí, 0 = no): ");
            tieneIVA = sc.nextInt();

            while (tieneIVA != 0 && tieneIVA != 1) {
                System.out.println("Error: solo se acepta 1 (sí) o 0 (no).");
                System.out.print("¿El producto tiene IVA? (1 = sí, 0 = no): ");
                tieneIVA = sc.nextInt();
            }

            // 4. Cálculos
            double iva = 0;
            if (tieneIVA == 1) {
                iva = 0.12 * precioBase; // IVA del 12%
            }

            double imc = 0.015 * precioBase; // IMC del 1.5%
            double precioFinal = precioBase + iva + imc;

            // Acumular totales del día
            totalProductos++;
            totalIVA += iva;
            totalIMC += imc;
            totalVentas += precioFinal;

            // 6. Mostrar datos del producto
            System.out.println("\nResumen del producto registrado:");
            System.out.println("Precio base: " + precioBase);
            System.out.println("IVA aplicado: " + iva);
            System.out.println("IMC aplicado: " + imc);
            System.out.println("Precio final: " + precioFinal);

            // Consumir el salto de línea pendiente antes del siguiente nombre
            sc.nextLine();
        }

        // 7. Resumen final del día
        System.out.println("\n===== RESUMEN DEL DÍA =====");
        System.out.println("Cantidad total de productos ingresados: " + totalProductos);
        System.out.println("Total recaudado en IVA: " + totalIVA);
        System.out.println("Total recaudado en IMC: " + totalIMC);
        System.out.println("Monto total de ventas (precios finales): " + totalVentas);

        sc.close();
    }
}