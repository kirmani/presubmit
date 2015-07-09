/*
 * Test.java
 * Copyright (C) 2015 Sean Kirmani <sean@kirmani.io>
 *
 * Distributed under terms of the MIT license.
 */

public class Test {
    public static final String CONSTANT = "constant";
    public Test() {
       System.out.println("Test");
    }
    public static void print(String text, boolean bool) {
        for (int i = 0; i < 100; i++) {
            for (int j = 0; j < 10; j++) {
                String hello = "Hello World";
                System.out.println(hello);
            }
        }
        System.out.println(text);
    }
}

