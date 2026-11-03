struct Reading
{
    int value;
    int quality;
};

void reset_reading(int reading_value)
{
    reading_value = 0;
}

int main()
{
    Reading sample{1, 2};
    reset_reading(sample.value);
    return 0;
}
