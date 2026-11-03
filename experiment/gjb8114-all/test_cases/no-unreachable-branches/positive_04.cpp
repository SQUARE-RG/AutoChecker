int main(void)
{
    unsigned int value = 200u;
    unsigned int seeds = 0u;

    // 逻辑与右侧的 "value <= 100u" 仍可能为假，两个分支均可达
    if (value >= 0u && value <= 100u)
    {
        seeds = 3u;
    }
    else
    {
        seeds = 7u;
    }

    return static_cast<int>(seeds);
}
