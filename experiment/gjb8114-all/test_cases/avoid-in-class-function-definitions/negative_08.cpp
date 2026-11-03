namespace registry {
class Config {
public:
    constexpr int default_value() const // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
    {
        return 17;
    }
};
}
int main() {
    registry::Config config;
    return config.default_value();
}
