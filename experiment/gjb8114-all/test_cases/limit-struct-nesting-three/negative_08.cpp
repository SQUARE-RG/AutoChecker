struct Host {
    struct Level2 {
        void build() {
            struct Level3 {
                struct Level4 {}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-5]
            };
        }
    };
};

int main() {
    Host::Level2 value;
    value.build();
    return 0;
}
