enum Weekday { sunday, monday };

int main()
{
    if (int chosen_day = 1; chosen_day > 0) {
        return chosen_day;
    }
    Weekday day = sunday;
    return static_cast<int>(day);
}
