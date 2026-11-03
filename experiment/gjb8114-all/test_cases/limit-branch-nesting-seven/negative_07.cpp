void negative_07(int x) {
    if (x > 0) {
        x -= 1;
    } else {
        if (x > 1) {
            if (x > 2) {
                if (x > 3) {
                    if (x > 4) {
                        if (x > 5) {
                            if (x > 6) {
                                if (x > 7) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-4-1]
                                    x += 1;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
