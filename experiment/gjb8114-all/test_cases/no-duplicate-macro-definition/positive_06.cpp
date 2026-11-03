#define ENGINE_SPEED_LIMIT 120

static int limit_speed(int requested)
{
    if (requested > ENGINE_SPEED_LIMIT)
    {
        return ENGINE_SPEED_LIMIT;
    }
    return requested;
}

int main()
{
    return limit_speed(130);
}
