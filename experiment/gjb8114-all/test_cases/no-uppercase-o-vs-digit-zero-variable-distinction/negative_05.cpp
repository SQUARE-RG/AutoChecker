class SpeedConfig {
public:
    static int fSpeedO;
    static int fSpeed0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
};

int main() {
    return 0;
}
