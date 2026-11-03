class Config {
public:
    static int fSpeedl;
    static int fSpeed1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-9]
};

int Config::fSpeedl = 10;
int Config::fSpeed1 = 20;
