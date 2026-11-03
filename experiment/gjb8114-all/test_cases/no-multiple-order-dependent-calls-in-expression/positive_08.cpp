unsigned int Bump(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x + 1;
    return x;
}

unsigned int Dec(unsigned int *pcData)
{
    unsigned int x = *pcData;
    *pcData = x - 1;
    return x;
}

int main()
{
    unsigned int state = 10;
    unsigned int first = Bump(&state), second = Dec(&state);
    return static_cast<int>(first + second);
}
