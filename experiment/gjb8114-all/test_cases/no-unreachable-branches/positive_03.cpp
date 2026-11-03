int main(void)
{
    unsigned int level = 0u;
    unsigned int selected = 0u;

    // 无符号整数与 0 做 <= 比较，零值与非零值分别覆盖两个分支
    if (level <= 0u)
    {
        selected = 10u;
    }
    else
    {
        selected = 20u;
    }

    return static_cast<int>(selected);
}
