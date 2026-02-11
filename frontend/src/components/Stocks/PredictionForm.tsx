import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { usePrediction } from "@/hooks/useInference"
import type { PredictionHorizon } from "@/types"

const horizonOptions: { value: PredictionHorizon; label: string }[] = [
  { value: "1h", label: "1 Hour" },
  { value: "4h", label: "4 Hours" },
  { value: "1d", label: "1 Day" },
  { value: "1w", label: "1 Week" },
]

const formSchema = z.object({
  horizon: z.enum(["1h", "4h", "1d", "1w"]),
})

type FormData = z.infer<typeof formSchema>

interface PredictionFormProps {
  symbol: string
}

export function PredictionForm({ symbol }: PredictionFormProps) {
  const mutation = usePrediction()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      horizon: "1d",
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate({ symbol, horizon: data.horizon })
  }

  const result = mutation.data

  return (
    <div className="flex flex-col gap-6">
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex items-end gap-4"
        >
          <FormField
            control={form.control}
            name="horizon"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Prediction Horizon</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Select horizon" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {horizonOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <LoadingButton type="submit" loading={mutation.isPending}>
            Predict
          </LoadingButton>
        </form>
      </Form>

      {mutation.isError && (
        <p className="text-sm text-destructive">
          Failed to get prediction. Please try again.
        </p>
      )}

      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Prediction Result</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-muted-foreground">Current Price</dt>
                <dd className="text-2xl font-bold font-mono">
                  ${result.current_price.toFixed(2)}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Predicted Price (60d)</dt>
                <dd className="text-2xl font-bold font-mono">
                  ${result.predicted_price.toFixed(2)}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Expected Return</dt>
                <dd className={`text-2xl font-bold font-mono ${result.predicted_return >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {result.predicted_return >= 0 ? '+' : ''}{result.predicted_return.toFixed(2)}%
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Prediction Date</dt>
                <dd className="font-mono">
                  {new Date(result.prediction_date).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Model Version</dt>
                <dd className="font-mono text-xs">{result.model_version}</dd>
              </div>
              {result.confidence !== null && (
                <div>
                  <dt className="text-muted-foreground">Confidence</dt>
                  <dd className="text-2xl font-bold font-mono">
                    {(result.confidence * 100).toFixed(1)}%
                  </dd>
                </div>
              )}
            </dl>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
