int main(void)
{
    unsigned int counter = 0u;
    unsigned int result = 0u;

    // 无符号减法表达式的结果与 0 做 >= 比较，条件恒为真
    if (counter - 1u >= 0u)
    {
        result = 1u;
    }
    else
    {
        result = 2u; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-2]
    }

    return 0;
}
