#include <stop_token>
#include <utility>
#include <uring_exec.hpp>

int main() {
    uring_exec::io_uring_exec ctx({.uring_entries = 8});
    auto scheduler = ctx.get_scheduler();

    auto sender = uring_exec::async_nop(scheduler);
    (void)sender;

    return 0;
}
