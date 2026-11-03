int drain(int value)
{
    while (1)
    {
        if (value <= 0)
        {
            return 0;
        }
        value -= 1;
    }
}

int main(void)
{
    return drain(3);
}
