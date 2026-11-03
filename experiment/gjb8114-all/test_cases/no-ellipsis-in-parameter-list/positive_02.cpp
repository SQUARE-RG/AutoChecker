class Formatter {
public:
    int format(int value, int width) const
    {
        return value * width;
    }
};

int main()
{
    Formatter formatter;
    return formatter.format(7, 3);
}
