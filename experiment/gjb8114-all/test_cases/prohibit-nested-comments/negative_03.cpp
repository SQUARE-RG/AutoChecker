struct Config {
    int enabled;

    /* default /* fallback */ // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
    int level;
};

int main() {
    Config c{1, 2};
    return c.enabled + c.level;
}
