bool is_enabled(int mode);

int main()
{
    bool enabled = is_enabled(1);
    return enabled ? 0 : 1;
}

bool is_enabled(int mode)
{
    int state = mode + 1;
    if (mode > 0)
    {
        return state; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
    }
    return false;
}
