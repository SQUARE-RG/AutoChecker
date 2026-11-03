void build_local_types() {
    struct Level0 {
        struct Level1 {
            struct Level2 {
                struct Level3 { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
                    int value;
                };
            };
        };
    };
}
