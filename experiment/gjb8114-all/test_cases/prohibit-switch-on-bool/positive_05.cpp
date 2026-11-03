int main()
{
    bool flag = true;
    int y = 0;
    switch (static_cast<int>(flag))
    {
        case 0:
            y = 1;
            break;
        case 1:
            y = 2;
            break;
    }
    return y;
}
