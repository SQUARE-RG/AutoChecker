struct ServiceConfig {
    static inline int timeoutSeconds = 30; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-11-2]
};

int main() {
    return ServiceConfig::timeoutSeconds == 30 ? 0 : 1;
}
