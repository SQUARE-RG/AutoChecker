enum SwitchState
{
    StateOff = 0,
    StateOn = 1
};

int main()
{
    const bool enabled = true;
    unsigned int data = enabled ? StateOn : 0u; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-11]
    (void)data;
    return 0;
}
