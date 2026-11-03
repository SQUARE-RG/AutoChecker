struct POINTA
{
    unsigned int x;
    unsigned int y;
};

int main(void)
{
    unsigned int pot_y = 1;
    POINTA pot_a;
    pot_a.y = pot_y;
    return static_cast<int>(pot_a.y);
}
