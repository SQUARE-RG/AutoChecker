typedef int SINT_32;

class Config {
public:
    int count;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    SINT_32 level;
};

SINT_32 main() {
    Config config{0, 0};
    return config.count + config.level;
}
