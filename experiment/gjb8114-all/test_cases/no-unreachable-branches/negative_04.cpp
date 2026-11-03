int main(void)
{
    unsigned int index = 0u;
    unsigned int flag = 0u;
    unsigned int state = 0u;

    // 逻辑或左侧的 "index >= 0u" 恒为真，整体条件恒真
    if (index >= 0u || flag == 1u)
    {
        state = 1u;
    }
    else
    {
        state = 2u; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }

    return static_cast<int>(state);
}
