template <typename T>
struct TemplateOuter {
    struct Level1 {
        struct Level2 {
            struct Level3 { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
                T value;
            };
        };
    };
};

int main() {
    return 0;
}
