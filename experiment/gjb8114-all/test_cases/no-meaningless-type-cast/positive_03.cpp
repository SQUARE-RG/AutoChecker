int main()
{
    double value = 3.9;
    unsigned int truncated = static_cast<unsigned int>(value);
    return truncated == 3u ? 0 : 1;
}
