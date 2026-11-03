enum Command { Start, Stop, Reset };

int main()
{
    Command cmd = Start;
    unsigned int code = 0u;
    switch (cmd)
    {
    case Start:
        code = 1u;
        break;
    case Stop:
        code = 2u;
        break;
    case Reset:
        code = 3u;
        break;
    }
    return static_cast<int>(code);
}
