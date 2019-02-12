
function lock {
    gpio write 7 1
    sleep $1
    gpio write 7 0
    sleep $2
}

lock 0.5 0.5
lock 0.5 0.5

lock 0.25 0.25
lock 0.25 0.25
lock 0.25 0.75

lock 0.25 0.25
lock 0.25 0.25
lock 0.25 0.25
lock 0.25 0.75

lock 0.25 0.25
lock 0.25 0.25
