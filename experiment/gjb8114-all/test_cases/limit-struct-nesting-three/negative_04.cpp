class Container {
public:
    struct Level1 {
        struct Level2 {
            struct Level3 {
                struct Level4 { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
                    int value;
                };
            };
        };
    };
};
