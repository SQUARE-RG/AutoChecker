struct Config {
    inline static int const value = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
};

int main() {
    return Config::value;
}
