enum Mode
{
    MODE_OFF,
    MODE_ON
};

int main()
{
    int Mode = MODE_ON; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    Mode = Mode + 1;
    return Mode;
}
