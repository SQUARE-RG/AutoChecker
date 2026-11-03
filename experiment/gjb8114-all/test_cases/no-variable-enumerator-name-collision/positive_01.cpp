enum Name_type { first = 0, second };

int main()
{
    unsigned int second_value = 0;
    Name_type current = second;
    (void)current;
    return static_cast<int>(second_value);
}
