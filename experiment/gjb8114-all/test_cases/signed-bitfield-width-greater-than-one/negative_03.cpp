class Config {
public:
    signed int flag : 1;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-10]
    signed int level : 4;
};

int main(void)
{
    Config cfg;
    cfg.flag = -1;
    cfg.level = 3;
    return 0;
}
