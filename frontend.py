from multiprocessing import Queue
from threading import Lock
from itertools import product
import json

queue = Queue()
queue_lock = Lock()


def main():
    combine()


def combine():
    replications = 1
    model_names = ['alexnet', 'mobilenet_v3_large',
                   'mobilenet_v3_small', 'resnet18', 'resnet101', 'vgg11', 'vgg19']
    epochs = [5, 10]
    learning_rates = [0.001, 0.0001, 0.00001]
    weight_decays = [0, 0.0001]

    combinations = list(product(model_names, epochs,
                        learning_rates, weight_decays))

    for model_name, epochs, learning_rate, weight_decay in combinations:
        json_data = json.dumps({
            "replications": replications,
            "model_name": model_name,
            "epochs": epochs,
            "learning_rate": learning_rate,
            "weight_decay": weight_decay
        }, indent=4)  # string
        queue.put(json_data)


def processRequest(receivedJson):
    with queue_lock:
        status = receivedJson.get('status')
        if status in ['ONLINE', 'FINISHED']:
            combinations = []
            if status == 'FINISHED':
                print("Retorno do worker: " + json.dumps(receivedJson))
                with open("results.txt", "a") as file:
                    file.write(json.dumps(receivedJson) + "\n")
                if not queue.empty():
                    item = queue.get()
                    combinations.append(item)
                    data_to_send = {
                        "machine_id": "server", "data": combinations}

                    # json_loads = json.loads(data_to_send)
                    data_to_send["data"] = [json.loads(
                        item) for item in data_to_send["data"]]
                    json_result = json.dumps(data_to_send, indent=4)

                    print("Retorno do json_result: " + json_result)

                    return json_result
                else:
                    return None

            if status == 'ONLINE':
                num_cores = receivedJson.get('num_cores')
                if num_cores:
                    for _ in range(num_cores):
                        if not queue.empty():
                            combinations.append(queue.get())
                        else:
                            break

                    data_dict = {"machine_id": "server", "data": combinations}

                    data_dict["data"] = [json.loads(
                        item) for item in data_dict["data"]]

                    json_result = json.dumps(data_dict, indent=4)

                    return json_result


main()
